import os
from github import Github, Auth

def get_repo_files(owner, repo, branch="main", extensions=(".py", ".js", ".ts", ".java")):
    token = os.getenv("GITHUB_TOKEN")
    gh = Github(auth=Auth.Token(token))
    repository = gh.get_repo(f"{owner}/{repo}")
    tree = repository.get_git_tree(branch, recursive=True)
    file_contents = {}
    for item in tree.tree:
        if item.type == "blob" and item.path.endswith(extensions):
            try:
                content = repository.get_contents(item.path, ref=branch)
                file_contents[item.path] = content.decoded_content.decode("utf-8", errors="ignore")
            except Exception:
                continue
    return file_contents