# Title of empty-wrapper / nested Index

"empty-wrapper" has no files of its own, only this "nested" subfolder.
hermesbaby's filesystem-toctree walk treats a folder with no document file
of its own as transparent rather than dropping it: "nested"'s own toctree
node (this file and "content.md") bubbles up directly into "empty-wrapper"'s
parent, sorted by "nested"'s own name.
