#include <cstdlib>
#include <cstdio>
#include <string>
#include <vector>
#include <iostream>

// dyninst libraries

#include "BPatch.h"
#include "BPatch_addressSpace.h"
#include "BPatch_process.h"
#include "BPatch_function.h"
#include "BPatch_point.h"
//#include "BPatch_flowGraph.h"

using namespace std;




int main(int argc, char **argv)
{
	BPatch bpatch1, bpatch2;
	int pid;
	BPatch_process *app_proc;
	BPatch_addressSpace *aspace;
	BPatch_image *image;
	
	// check the options
	if(argc != 2)
	{
		cerr << "ERROR ## Missing command line args. Use PID of the process you want to attach.\n";
		return 1;
	}

	pid = atoi(argv[1]);
	if(pid == 0)
	{
		cerr << "ERROR ## Wrong PID " << pid << ", please use another.\n";
		return 2;
	}

	cerr << "TAKE1 A\n";
	// let's go...
	app_proc = bpatch1.processAttach(NULL, pid);
	cerr << "TAKE1 B\n";
	aspace = app_proc;
	cerr << "TAKE1 C\n";
	image = aspace->getImage();
	cerr << "TAKE1 D\n";
	
/*	BPatch_Set<BPatch_opCode> access_types;
	access_types.insert(BPatch_opLoad);
	access_types.insert(BPatch_opStore);
*/
	vector<BPatch_function *> functions, incr_functions;
	vector<BPatch_point *> *points;
	image->findFunction("function_name", functions);
	cerr << "TAKE1 E\n";
	points = functions[0]->findPoint(BPatch_entry);
	cerr << "TAKE1 F\n";
	
	// create snippet
	image->findFunction("incr", incr_functions);
	cerr << "TAKE1 G\n";
	vector<BPatch_snippet *> incr_args;
	BPatch_funcCallExpr incr_call(*(incr_functions[0]), incr_args);
	
	aspace->insertSnippet(incr_call, *points);
	cerr << "TAKE1 H\n";
	app_proc->continueExecution();
	cerr << "TAKE1 I\n";
	sleep(4);
	app_proc->detach(true);

	cout << "FIRST MUTATION DONE. MUTATOR IS DOING THE SECOND ONE...\n";

	sleep(4);

	cerr << "TAKE2 A\n";
	// let's go...
	app_proc = bpatch2.processAttach(NULL, pid);
	cerr << "TAKE2 B\n";
	aspace = app_proc;
	cerr << "TAKE2 C\n";
	image = aspace->getImage();
	cerr << "TAKE2 D\n";
	
/*	BPatch_Set<BPatch_opCode> access_types;
	access_types.insert(BPatch_opLoad);
	access_types.insert(BPatch_opStore);
*/
	vector<BPatch_function *> functions2, incr_functions2;
	vector<BPatch_point *> *points2;;
	image->findFunction("function_name", functions2);
	cerr << "TAKE2 E\n";
	points2 = functions2[0]->findPoint(BPatch_exit);
	cerr << "TAKE2 F\n";
	
	// create snippet
	image->findFunction("incr2", incr_functions2);
	cerr << "TAKE2 G\n";
	vector<BPatch_snippet *> incr_args2;
	BPatch_funcCallExpr incr_call2(*(incr_functions2[0]), incr_args2);
	
	aspace->insertSnippet(incr_call2, *points2);
	cerr << "TAKE2 H\n";
	app_proc->continueExecution();
	cerr << "TAKE2 I\n";
	app_proc->detach(true);
	
	cout << "SECOND MUTATION DONE. MUTATOR IS GOING...\n";
	
	return 0;
}
