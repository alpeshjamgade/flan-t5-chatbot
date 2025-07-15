.PHONY: help install install-dev test lint format clean build run run-dev setup-env check-env

help:
	@echo "Available commands:"
	@echo "  install      Install the package"
	@echo "  install-dev  Install in development mode with dev dependencies"
	@echo "  setup-env    Set up development environment"
	@echo "  check-env    Check if environment is properly set up"
	@echo "  test         Run tests (when implemented)"
	@echo "  lint         Run linting (flake8)"
	@echo "  format       Format code (black)"
	@echo "  clean        Clean build artifacts"
	@echo "  build        Build distribution packages"
	@echo "  run          Run the installed application"
	@echo "  run-dev      Run in development mode (without installation)"

install:
	chmod +x install.sh
	./install.sh

install-dev:
	python3 -m venv .venv
	source .venv/bin/activate && pip install --upgrade pip
	source .venv/bin/activate && pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
	source .venv/bin/activate && pip install -e ".[dev]"

setup-env:
	@echo "🔧 Setting up development environment..."
	python3 -m venv .venv
	source .venv/bin/activate && pip install --upgrade pip
	source .venv/bin/activate && pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
	source .venv/bin/activate && pip install -r requirements.txt
	source .venv/bin/activate && pip install -e .
	mkdir -p conversations logs
	@echo "✅ Development environment set up!"
	@echo "Activate with: source .venv/bin/activate"

check-env:
	@echo "🔍 Checking environment..."
	@if [ ! -d ".venv" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup-env' first."; \
		exit 1; \
	fi
	@source .venv/bin/activate && python3 -c "import torch; print('✅ PyTorch:', torch.__version__)" || { \
		echo "❌ PyTorch not installed properly"; \
		exit 1; \
	}
	@source .venv/bin/activate && python3 -c "import flan_t5_chatbot; print('✅ Package installed successfully')" || { \
		echo "❌ Package not installed. Run 'make setup-env' first."; \
		exit 1; \
	}
	@echo "✅ Environment is properly set up!"

test:
	@echo "Tests not implemented yet"

lint:
	@if [ -d ".venv" ]; then \
		source .venv/bin/activate && flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics || true; \
		source .venv/bin/activate && flake8 src/ --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics || true; \
	else \
		echo "❌ Virtual environment not found. Run 'make setup-env' first."; \
	fi

format:
	@if [ -d ".venv" ]; then \
		source .venv/bin/activate && black src/ || true; \
	else \
		echo "❌ Virtual environment not found. Run 'make setup-env' first."; \
	fi

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: clean
	@if [ -d ".venv" ]; then \
		source .venv/bin/activate && python -m build || python setup.py sdist bdist_wheel; \
	else \
		echo "❌ Virtual environment not found. Run 'make setup-env' first."; \
	fi

run: check-env
	chmod +x run.sh
	./run.sh

run-dev: check-env
	@echo "🚀 Running in development mode..."
	source .venv/bin/activate && python3 run_dev.py

run-direct: check-env
	@echo "🚀 Running directly..."
	source .venv/bin/activate && python3 flan_t5_chat.py
