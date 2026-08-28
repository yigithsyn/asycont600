import argparse
import sys

from asycont600 import Asycont600_2, axes


def app():
    if len(sys.argv)>1 and sys.argv[1] == "move":
        parser = argparse.ArgumentParser(prog="move", description="Move Axis")
        parser.add_argument("axis", help="axis name [x, y, z, autslide, azimuth, pol]", type=str, nargs=1)
        parser.add_argument("pos", help="position", type=float, nargs=1)
        parser.add_argument("--absolute", help="absolutely position", action="store_true")
        try:
            args = parser.parse_args(sys.argv[2:])
        except Exception as e:
            print(parser.format_help())
            print(str(e))
            sys.exit()
        cont = Asycont600_2()
        cont.connect()
        cont.move(args.axis[0], args.pos[0], "absolute" if args.absolute else "relative", "slow")
    elif len(sys.argv)>1 and sys.argv[1] == "position":
        parser = argparse.ArgumentParser(prog="position", description="Get Current Position")
        parser.add_argument("axis", help="axis name [x, y, z, autslide, azimuth, pol]", type=str, nargs="?")
        parser.add_argument("--absolute", help="absolutely position", action="store_true")
        try:
            args = parser.parse_args(sys.argv[2:])
        except Exception as e:
            print(parser.format_help())
            print(str(e))
            sys.exit()
        cont = Asycont600_2()
        cont.connect()
        # If args.axis is None call position function without arguments otherwise supply axis info
        if args.axis is None:
            print(cont.position())
        else:
            print(cont.position(args.axis))
    elif len(sys.argv)>1 and sys.argv[1] == "stop":
        parser = argparse.ArgumentParser(prog="move", description="Move Axis")
        parser.add_argument("axis", help="axis name [x, y, z, autslide, azimuth, pol]", type=str, nargs="?")
        try:
            args = parser.parse_args(sys.argv[2:])
        except Exception as e:
            print(parser.format_help())
            print(str(e))
            sys.exit()
        if args.axis and len(args.axis) > 0:
            print(args.axis)
            cont = Asycont600_2()
            cont.connect()
            cont.stop(args.axis[0])
        else:
            for axis in axes:
                print(axis)
            cont = Asycont600_2()
            cont.connect()
            for axis in axes:
                cont.stop(axis)
        cont.disconnect()
  # elif len(sys.argv)>1 and sys.argv[1] == "server":
  #   parser = argparse.ArgumentParser(prog="server", description="Start HTTP Server")
  #   parser.add_argument("--port", help="tcp port number", default="7001", type=float, nargs=1)

  #   try:
  #     args = parser.parse_args(sys.argv[2:])
  #   except:
  #     print(parser.format_help())
  #     exit()
  #   cont = Asycont600_2()
  #   cont.connect()
    
  #   app = Flask(__name__)

  #   @app.route("/move/rel")
  #   def move():
  #     # cont.move(axis, pos, "absolute")
  #     return {"status": 0}

  #   @app.route("/move/rel/<axis>")
  #   def move_ax(axis: str):
  #     return axis

  #   @app.route("/move/abs/<axis>/<float:pos>")
  #   def move_abs(axis: str, pos: float):
  #     cont.move(axis, pos, "absolute")
  #     return {"status": 0}

  #   @app.route("/move/rel/<axis>/<pos>")
  #   def move_rel(axis: str, pos):
  #     cont.move(axis, float(pos), "relative")
  #     return {"status": 0}

  #   app.run()
    else:
        parser = argparse.ArgumentParser(prog="asycont600", description="ASYCONT600 Command line Utility")
        parser.add_argument("move", help="move axis", type=str, nargs="?")
        parser.add_argument("position", help="get current position", type=str, nargs="?")
        parser.add_argument("stop", help="stop axis", type=str, nargs="?")
        print(parser.format_help().replace("positional arguments","module/function").replace("[move] ","").replace("[stop] ","").replace("[swr2gamma] ","").replace("[wlen2freq] ","").replace("[measurement] ","").replace("[propagation] ","").replace("[propagation]","[module/function]"))

if __name__ == "__main__":
  app()
