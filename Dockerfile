# Pull base image
FROM python:3.10-bookworm

WORKDIR /app
# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
#RUN pip3 install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r ./requirements.txt
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org poetry
RUN poetry self add poetry-plugin-export
COPY ./app/pyproject.toml ./app/poetry.lock* /app/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

#COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

RUN apt-get update 
RUN apt-get install wkhtmltopdf -y
RUN apt install 

COPY ./app /app
EXPOSE 8000

#CMD ["uvicorn", "main:app" ,"--host", "0.0.0.0", "--port", "8080", "--reload"]


