# --- Imports ---
import numpy as np
import pandas as pd
import argparse
import re
import csv

# --- Define args ---
parser = argparse.ArgumentParser()
parser.add_argument('input_filename')
parser.add_argument('output_filename')
parser.add_argument('chapter')
args = parser.parse_args()

# --- Read input file ---
with open(args.input_filename) as file:
	lines = [line.rstrip() for line in file]
qSr = pd.Series(lines) 

# --- Map each line of inut file to new row in Pandas dataframe ---
curQPos = np.zeros(qSr.size)
pHList = curQPos
for q in np.arange(17,66):							# horrible looping inefficency grossness
	curQPos = map(sum, zip(curQPos,qSr.str.contains(pat = str(q) + '.\\xa0')))

# --- Identify rows that are questions, parse answer info for subsequent rows, 
# --- make new columns for that info, populate that info next to respective querstion ---
qDf = pd.DataFrame(list(zip(curQPos, qSr)), columns =['isQuestion', 'value'])
for idx in np.arange(len(qDf)):
	if qDf.loc[idx, 'isQuestion'] == 1:
		patterns = ["ANSWER:\\xa0\\xa0\\r(.+?)\\r","POINTS:\\xa0\\xa0\\r(.+?)\\r","\\ra.\\xa0\\r(.+?)\\r","\\rb.\\xa0\\r(.+?)\\r","\\rc.\\xa0\\r(.+?)\\r","\\rd.\\xa0\\r(.+?)\\r","\\re.\\xa0\\r(.+?$)"]
		qDf.at[idx,'correctAnswer'] = re.search(patterns[0], qDf.loc[idx + 2, 'value']).group(1)
		qDf.at[idx,'correctPoints'] = re.search(patterns[1], qDf.loc[idx + 2, 'value']).group(1)
		qDf.at[idx,'A'] = re.search(patterns[2], qDf.loc[idx + 1, 'value']).group(1)
		qDf.at[idx,'B'] = re.search(patterns[3], qDf.loc[idx + 1, 'value']).group(1)
		qDf.at[idx,'C'] = re.search(patterns[4], qDf.loc[idx + 1, 'value']).group(1)
		qDf.at[idx,'D'] = re.search(patterns[5], qDf.loc[idx + 1, 'value']).group(1)
		qDf.at[idx,'E'] = re.search(patterns[6], qDf.loc[idx + 1, 'value']).group(1)
qDf = qDf[qDf['isQuestion']==1]

# --- Generate .csv ---
qNp = qDf.rename_axis('ID').values
qToCSV = np.empty([1,3])
i = 0
for q in qNp:
	i+=1
	rowHeads = ["//MULTIPLE CHOICE QUESTION TYPE","//Options must include text in column3",
			"NewQuestion","ID","Title","QuestionText","Points","Difficulty","Image",
			"Option","Option","Option","Option","Option","Hint","Feedback",""]
	w = np.array(["","","MC","GEOG2250","Chapter"+str(args.chapter)+"-" + str(i),q[1],"1","1","",[0,1][q[2]=="a"],[0,1][q[2]=="b"],
				[0,1][q[2]=="c"],[0,1][q[2]=="d"],[0,1][q[2]=="e"],"","",""])
	x = np.array(["","","","","","","","","",q[4],q[5],q[6],q[7],q[8],"","",""])
	z = np.vstack((rowHeads,(np.vstack((w.T,x.T))))).T
	qToCSV = np.vstack((qToCSV,z))

with open(args.output_filename,'wb') as result_file:
    wr = csv.writer(result_file, dialect='excel')
    wr.writerows(qToCSV[2:])