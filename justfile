list:
    just --list

run arg1="":
    uv run src/manage.py runserver  {{arg1}}

test arg1="":
    uv run -m pytest {{arg1}}
