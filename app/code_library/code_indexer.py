import os
import git
import chromadb
import hashlib
import datetime
from langchain.embeddings.openai import OpenAIEmbeddings

class CodeIndexer:
    """Indexes source code from repositories and generates embeddings for retrieval."""

    def __init__(self, db_path="chroma_index"):
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.collection = self.chroma_client.get_or_create_collection(name="source_code")
        self.embeddings_model = OpenAIEmbeddings()

    def process_repository(self, repo_url, repo_dir):
        """
        Clones or updates the repository.

        Args:
            repo_url (str): Repository URL.
            repo_dir (str): Local path for the repository.

        Returns:
            git.Repo: Repository object.
        """
        if os.path.exists(repo_dir):
            repo = git.Repo(repo_dir)
            repo.remotes.origin.pull()
        else:
            repo = git.Repo.clone_from(repo_url, repo_dir)
        return repo

    def get_repo_metadata(self, repo):
        """
        Retrieves repository metadata, such as the branch and the current commit date.

        Args:
            repo (git.Repo): Repository object.

        Returns:
            dict: Dictionary with metadata.
        """
        branch = repo.active_branch.name
        commit_date = datetime.datetime.fromtimestamp(repo.head.commit.committed_date)
        # We use the current commit date for creation and update (this can be improved)
        return {
            "branch": branch,
            "creation_date": str(commit_date),
            "update_date": str(commit_date),
        }

    def load_code(self, repo_dir, extensions=[".py", ".js", ".java"]):
        """
        Loads the content of files with the specified extensions.

        Args:
            repo_dir (str): Repository path.
            extensions (list, optional): List of file extensions. Defaults to [".py", ".js", ".java"].

        Returns:
            dict: Dictionary with the file path as the key and content as the value.
        """
        code = {}
        for dp, _, filenames in os.walk(repo_dir):
            for f in filenames:
                if f.lower().endswith(tuple(ext.lower() for ext in extensions)):
                    file_path = os.path.join(dp, f)
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                            code[file_path] = file.read()
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
        return code

    def index_code(self, repo_url, repo_dir):
        """
        Indexes the repository's source code, generating embeddings and storing them in ChromaDB.

        Args:
            repo_url (str): Repository URL.
            repo_dir (str): Local path for the repository.
        """
        repo = self.process_repository(repo_url, repo_dir)
        repo_metadata = self.get_repo_metadata(repo)
        source_code = self.load_code(repo_dir)

        for file, content in source_code.items():
            # Includes repo_url in the hash to avoid collisions between files from different repositories
            doc_id = hashlib.md5((repo_url + file).encode()).hexdigest()
            embedding = self.embeddings_model.embed_documents([content])[0]
            metadata = {
                "file": file,
                "repo_url": repo_url,
                "branch": repo_metadata["branch"],
                "creation_date": repo_metadata["creation_date"],
                "update_date": repo_metadata["update_date"],
            }
            self.collection.add(ids=[doc_id], embeddings=[embedding], metadatas=[metadata])
        print(f"Repository {repo_url} successfully indexed!")

    def add_repositories(self, repo_list):
        """
        Indexes a list of repositories.

        Args:
            repo_list (list): List of repository URLs.
        """
        # Creates the 'repositories' directory if it doesn't exist
        if not os.path.exists("repositories"):
            os.makedirs("repositories")
        for repo_url in repo_list:
            repo_dir = os.path.join("repositories", hashlib.md5(repo_url.encode()).hexdigest())
            self.index_code(repo_url, repo_dir)

    def retrieve_code(self, question, top_k=3):
        """
        Retrieves relevant code snippets based on a query.

        Args:
            question (str): Query or search term.
            top_k (int, optional): Number of results. Defaults to 3.

        Returns:
            str: String containing code snippets and their respective metadata.
        """
        query_vector = self.embeddings_model.embed_documents([question])[0]
        results = self.collection.query(query_embeddings=[query_vector], n_results=top_k)
        
        # Handles the case where results are in a list of lists format
        documents = results["documents"][0] if results["documents"] and isinstance(results["documents"][0], list) else results["documents"]
        metadatas = results["metadatas"][0] if results["metadatas"] and isinstance(results["metadatas"][0], list) else results["metadatas"]

        snippets = []
        for doc, metadata in zip(documents, metadatas):
            file = metadata.get("file", "Unknown")
            snippets.append(f"File: {file}\nCode:\n{doc}\n---")
        return "\n".join(snippets)
