import sys
import csv
import argparse
import os
import time
from subprocess import call, PIPE

def main():
	start = time.time()

	# parse input arguments
	parser = argparse.ArgumentParser(description='Wrapper to run Genius from SMAC')
	parser.add_argument('instance', type=int,  help='instance')
	parser.add_argument('specifics', type=int,  help='specifics')
	parser.add_argument('cutoff', type=float,  help='cutoff')
	parser.add_argument('runlength', type=float,  help='runlength')
	parser.add_argument('seed', type=int,  help='seed')
	parser.add_argument('params', nargs=argparse.REMAINDER, help='-param1 value1 -param2 value2 [...]')
	
	args = parser.parse_args()

	# write the xml tournament setup
	write_xml(args.params[1::2])

	# call genius with tournament setup; surpress output
	devnull = open(os.devnull, 'w')
	call(["java", "-cp", "genius-8.0.0.jar", "genius.cli.Runner", "../runfiles/tournament.xml", "../logs/output"], cwd = "genius-8.0.0",
			stdout=devnull, stderr=devnull) 

	# process genius output file
	status, quality = getdatafromcsv("logs/output.csv")

	# calculate total runtime
	end = time.time()
	runtime = end - start

	# print output for SMAC algorithm
	print("Result for SMAC: {}, {}, {}, {}, {}".format(status, runtime, args.runlength, quality, args.seed))



def getdatafromcsv(file):
	#open the csv file
	csvFile = open(file,"r")
	reader = csv.reader(csvFile,delimiter=";")
	#csvFile.close()

	#Store the result in the 'utilities.csv' at the specific.position
	#csvFile2=open("logs/utilities.csv","w",newline='')
	#writer=csv.writer(csvFile2)
	index_agents = []
	index_utils = []
	result = []

	# init variables
	social_welfare = 0.0
	utility = 0.0
	count = 0

	for row in reader:
		if reader.line_num > 1:
			if reader.line_num == 2:
				for item in row:
					# save column indices of useful data
					if item == "Social Welfare":
						index_sw = row.index(item)
					if item[:5] == "Agent":
						index_agents.append(row.index(item))
					if item[:7] == "Utility":
						index_utils.append(row.index(item))
			else:
				for item in row:
					# find utility that corresponds to produced agent
					if item[:3] == "boa":
						social_welfare += float(row[index_sw])
						utility += float(row[row.index(item)-min(index_agents)+min(index_utils)])
						count += 1


	#result.append([float(row[i]) for i in index])
	# check if the data is correct
	#print(result)
	#writer.writerow(result)
	csvFile.close()
	#csvFile2.close()

	# return result
	if count == 0:
		return ("CRASHED", 6.0)
	else:
		return ("SUCCESS", 1-(utility/count))



def write_xml(BOAcomps):
	# open tournament template and read
	f = open("runfiles/tournament_template.xml", "r")
	contents = f.readlines()
	f.close()

	# add customized agent components
	contents[16] = '<item classpath="negotiator.boaframework.offeringstrategy.{}"/>\n'.format(BOAcomps[0])
	contents[19] = '<item classpath="negotiator.boaframework.acceptanceconditions.{}"/>\n'.format(BOAcomps[1])
	contents[22] = '<item classpath="negotiator.boaframework.opponentmodel.{}"/>\n'.format(BOAcomps[2])
	contents[25] = '<item classpath="negotiator.boaframework.omstrategy.{}"/>\n'.format(BOAcomps[3])

	# delete old tournament file and write new
	f = open("runfiles/tournament.xml", "w")
	contents = "".join(contents)
	f.write(contents)
	f.close()

# Check if wrapper is called via command line
if __name__ == "__main__":
	main()

