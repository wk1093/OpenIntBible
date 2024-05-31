# OpenIntBible

Open Interlinear Bible

## Description

A Website that contains the entire bible in greek/hebrew with english translation.
The website is built using Flask and pure HTML/CSS/JS. Hosted with PythonAnywhere (for now)
[here](https://wyattk1093.pythonanywhere.com/).

## Credits

 - [Wyatt Kloos](https://github.com/wk1093) (Me) - Developer of [OpenIntBible](https://github.com/wk1093/OpenIntBible)
 - [Eliran Wong](https://github.com/eliranwong) - Creator of [OpenHebrewBible](https://github.com/eliranwong/OpenHebrewBible) and [OpenGNT](https://github.com/eliranwong/OpenGNT)
 - [Flask](https://flask.palletsprojects.com/) - The web framework used
 - [PythonAnywhere](https://www.pythonanywhere.com/) - Hosting service used

## License

This project is completely open source and free to use and/or modify. Please give credit where credit is due (Not required but appreciated).

## Installation

To run this project locally, you will need to have Python installed on your machine. You can download it [here](https://www.python.org/downloads/).

1. Clone the repository
```bash
git clone https://github.com/wk1093/OpenIntBible.git
```

2. Install the required packages
```bash
pip install -r requirements.txt
```

3. Run the application (This will start a local server on your machine, WARNING: This is a debug server and should not be used in production)
```bash
python main.py
```

Optionally, you can run the application using a more secure and "production ready" server using the following command
```bash
gunicorn main:app
```

Which requires the `gunicorn` package to be installed. You can install it using the following command
```bash
pip install gunicorn
```


## Contributing

If you would like to contribute to this project, please feel free to fork the repository and submit a pull request. I will review the changes and merge them if they are appropriate.

If I don't respond to your pull request within a week, please feel free to reach out to me at [wyattk1093@gmail.com](mailto:wyattk1093@gmail.com) or on discord at `banana1093`.
