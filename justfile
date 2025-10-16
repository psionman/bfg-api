list:
    just --list

run:
    uv run src/manage.py runserver

test arg1="":
    uv run -m pytest {{arg1}}
