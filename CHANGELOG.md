# Changelog

## 2.0.0 (2021-05-11) 

- Rename from  `campaign-tree-editor` to `mara-campaign-tree-editor`
- Move from Project A internal repository to Github
- Add README.md

**required changes**

In your `requirements.txt`, change 

```
-e git+ssh://git@codebasehq.com/project-a/mara/campaign-tree-editor.git@master#egg=campaign-tree-editor
```
to
```
-e git+https://github.com/project-a/mara-campaign-tree-editor.git@2.0.0#egg=mara-campaign-tree-editor
```