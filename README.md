## About

This is a project for EC504 at Boston University.  This project uses Locality-Sensitive Hashing and KD-Trees to search geospatial data.  Specificaly, given latitude and longitude coordinates (and ultimately additional dimensions, such as elevation, height, etc.), the program will return zip codes near those coordinates. 


## Running with Docker

Additional information about installing Docker can be found here: https://docs.docker.com/engine/install/

With Docker installed, run the following command from the root directory to build the image, run the container, and run the programming, printing the result to the console.

```console
docker-compose up --build
```

## Running with Python Installation

### Dependencies

Additional information about installing Python can be found here: https://www.python.org/downloads/  

(Recommend Python 3.10, though later versions will likely work as well.)

Run the following setup a virtual environment in the root directory.

Mac: 
```console
python -m venv venv
source venv/bin/activate
```

Win:
```console
python -m venv venv
venv\Scripts\activate.bat
```

Run the following to install dependencies in the virtual environment.

```console
pip install -r requirements.txt
```

### Running Program

For now, the main entry point is the benchmark.py.  Run the following in the root directory to execute both the LSH and KD-Tree algorithms on some sample data (US zip codes and coordinates).  After a minute or so the program will print to the console their accuracies and run times. 

```console
python src/benchmark.py
```

## Unit Tests

(Needs to be developed more...)

From the root run the following run all unit tests with pytest:

```console
pytest
```

## Coverage

(Need to fix...)

```console
python -m coverage run -m pytest
python -m coverage [report | html]
```

## Example output

```console
(venv) $ python src/benchmark.py
Multi-Table LSH - Time: 0.04035s, Accuracy: 0.55
Approximate KD Tree - Time: 0.00011s, Accuracy: 0.08
```

## Contributors

Chris Krenz

## License

[MIT License](LICENSE)
