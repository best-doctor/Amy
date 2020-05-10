import typing

CommitInfo = typing.Mapping[str, typing.Any]
CommitDiffInfo = typing.Mapping[str, typing.Any]
Comment = typing.Mapping[str, typing.Any]
GroupedCommits = typing.Mapping[str, typing.List[CommitInfo]]
