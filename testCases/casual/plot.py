from zipfile import ZipFile
import matplotlib
matplotlib.use( 'Agg') # Needed because there is no display
import matplotlib.pyplot as plt
import csv
import sys

graphs = {}

# Parse csv data
for arg in range( 1, len( sys.argv)):
   with ZipFile( sys.argv[ arg], "r") as zip:
      for filename in zip.infolist():
         if( filename.filename.endswith( "history.csv")):
            csv_reader = csv.DictReader( zip.open( filename.filename))

            for row in csv_reader:
               graphs.setdefault( filename.filename, {}).setdefault( row[ "Name"], {}).setdefault( sys.argv[ arg], {}).setdefault( "Total Average Response Time", []).append( row[ "Total Average Response Time"])
               graphs.setdefault( filename.filename, {}).setdefault( row[ "Name"], {}).setdefault( sys.argv[ arg], {}).setdefault( "User Count", []).append( row[ "User Count"])
               graphs.setdefault( filename.filename, {}).setdefault( row[ "Name"], {}).setdefault( sys.argv[ arg], {}).setdefault( "Timestamp", []).append( row[ "Timestamp"])



for filename in graphs.keys():
   subplots = len( graphs[ filename].keys())
   fig, ax = plt.subplots( subplots, figsize = ( 10, 5 * subplots))

   for index, graphname in enumerate( graphs[ filename].keys()):
      ytop_lim = 0

      for zipfile in graphs[ filename][ graphname].keys():
         ax[ index].set_title( graphname)
         ax[ index].set_xlabel( "Test duration (ms)")
         ax[ index].set_ylabel( "Total average response time (ms)")

         y = graphs[ filename][ graphname][ zipfile][ "Total Average Response Time"]
         x = range( 0, len( y) * 1000, 1000)
         ax[ index].plot( x, y, label = zipfile)
         # ax[ index].legend()

         if( max( y) > ytop_lim):
            ytop_lim = max( y)

         # Y-axis for user count
         ax2 = ax[ index].twinx()
         ax2.set_ylabel( "User count")

         y =  graphs[ filename][ graphname][ zipfile][ "User Count"]
         x = range( 0, len( y) * 1000, 1000)
         line2 = ax2.plot( x, y, color = "black")
         
         ax[ index].set_ylim( bottom = 0, top = float( ytop_lim))
         ax2.set_ylim( 0, 15)

         handles, labels = ax[ 0].get_legend_handles_labels()
         handles = handles + line2
         labels = labels + [ "User count"]
         fig.legend( handles, labels)

   # print( graphs.keys()[ i].split( ".")[ 0] + ".png")
   plt.savefig( filename.split( ".")[ 0] + ".png")

