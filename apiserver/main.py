# sys.path.insert(0, './apiserver/')

from apiserver.api import app
from apiserver.views import create_views


def main():
    app.run(debug=True, port=8000, threaded=False)


app = create_views(app)

if __name__ == '__main__':
    main()
