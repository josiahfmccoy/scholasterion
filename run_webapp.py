import argparse
from webapp import create_app

application = create_app()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', default=5060)
    parser.add_argument('--expose', action="store_true", default=False)
    args = parser.parse_args()

    if args.expose:
        application.run(port=args.port, host='0.0.0.0')
    else:
        application.run(port=args.port)
