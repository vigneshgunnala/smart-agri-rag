.PHONY: install index run api test eval

install:
	pip install -r requirements.txt

index:
	python -c "from src.rag import build_index; print(len(build_index().chunks), 'chunks indexed')"

run:
	streamlit run app.py

api:
	uvicorn api:app --reload

test:
	pytest tests -q

eval:
	python -m src.evaluate --top-k 4
