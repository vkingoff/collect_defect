from git import Repo
from itertools import islice, chain
from subprocess import run, PIPE
import json

keywords = ['fix', 'bug', 'error', 'fail']

def is_contains_whole_word(message, word):
    message = message.replace('\n', ' ').lower()
    return message.startswith(word) or message.endswith(word) or ' {} '.format(word) in message


def is_corrective_commit(commit):
    return any(is_contains_whole_word(commit.message, keyword) for keyword in keywords)


def is_js_file(diff):
    return diff.a_path.startswith('src/') and diff.a_path.endswith('.js')


def iter_corrective_commits(commits):
    return (commit for commit in commits if is_corrective_commit(commit))


def _iter_corrective_diffs(commit):
    if not commit.parents:
        return ()
    commit_parent = commit.parents[0]
    modified_diffs = commit.diff(commit_parent).iter_change_type('M')
    return (diff for diff in modified_diffs if is_js_file(diff))


def iter_corrective_diffs(commits):
    return chain.from_iterable(_iter_corrective_diffs(commit) for commit in commits)


def _iter_functions(diff):
    a_data = diff.a_blob.data_stream.read().decode('utf-8')
    b_data = diff.b_blob.data_stream.read().decode('utf-8')
    print(diff.a_path)
    a_result = run(['node', 'analyse.js'], stdout=PIPE, input=a_data, universal_newlines=True)
    b_result = run(['node', 'analyse.js'], stdout=PIPE, input=b_data, universal_newlines=True)
    a_functions = json.loads(a_result.stdout)
    b_functions = json.loads(b_result.stdout)
    a_dict = { function['name'] : function for function in a_functions if function['name'] != '<anonymous>' }
    for b_function in b_functions:
        a_function = a_dict.get(b_function['name'])
        if a_function:
            if 'line' in a_function:
                del a_function['line']
            if 'line' in b_function:
                del b_function['line']
            if a_function != b_function:
                yield dict(a=a_function, b=b_function)


def iter_functions(diffs):
    return chain.from_iterable(_iter_functions(diff) for diff in diffs)
    

if __name__ == "__main__":
    repo = Repo("./data/atom")
    commits = repo.iter_commits('master')
    corrective_commits = iter_corrective_commits(commits)
    corrective_diffs = iter_corrective_diffs(corrective_commits)
    functions = iter_functions(corrective_diffs)
    for function in functions:
        print(json.dumps(function, indent=2))
        input()