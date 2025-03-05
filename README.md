# EasyCompare

1. This is a Sublime Text plugin.
2. It is primarily used to invoke external tools for quickly comparing two files.
3. Currently, it supports the Windows platform and can invoke TortoiseSVN, TortoiseGit, and WinMerge.
4. It allows comparison even if the files are not saved.
5. It supports "Compare Later" and "Compare With" features.


## Two Column Compare


## Compare Later


## Settings
`
{
    "default_tool": "tortoise_svn",
    "tortoise_svn_path": "C:\\Program Files\\TortoiseSVN\\bin\\TortoiseProc.exe",
    "tortoise_git_path": "C:\\Program Files\\TortoiseSVN\\bin\\TortoiseGitProc.exe",
    "win_merge_path": "C:\\Program Files\\WinMerge\\WinMergeU.exe"
}
`

default_tool: 'tortoise_svn', 'tortoise_git', 'win_merge'