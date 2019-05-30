
import sys

sys.path.insert(0, './apiserver')

from apiserver.main import app

if __name__ == '__main__':
    app.run(port=8000)
