# Agent 06：让 Agent 整理一段本地资料

本期承接第 5 期，把伪代码落成一个处理本地资料的可运行示例。

重点不是让 Agent 一开始就很聪明，而是先让变量来源清楚：

```text
source -> task -> state -> tools -> answer
```

对应代码：

- `agent_06_local_notes.py`
