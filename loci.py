
import itertools	# using slice() to skip over header line
import sys		    # using argv and exit()
import os.path		# using exists()
import time		    # using asctime()

def check_args(argv) -> bool :

    """
    Summary:

        Check the command-line arguments passed in.


    Parameters:

        argv (list): The argument vector

    Returns:

        True - All required parameters are there

        False- Failure in one or more checks

    Description:

        This function checks the command line arguments to ensure
        there are the correct amount and that the required input
        files are present.
    """

    num_args = len(argv)	# the number of args presented on the cmd-line

    status = True	    	# assume success

    if (num_args != 4):		# correct number of args?

        print( "Usage: python3 loci.py <loci pathname> <reads pathname> <output pathname>" )
        status = False
    else:

        if os.path.exists(argv[1]) == False:	# loci file input file missing?

            print(sys.argv[1], "does not exist or isn't a file.")
            status = False

        if os.path.exists(argv[2]) == False:	# reads file input file missing?

            print(sys.argv[2], "does not exist or isn't a file.")
            status = False

    if ( status == True ):	        			# display args passed in

        print()
        print( "Loci from:  ", sys.argv[1] )
        print( "Reads from: ", sys.argv[2] )
        print( "Output to:  ", sys.argv[3] )

    return status


def init_poscov(loci_pathname, loci):
    """
    Summary:

        Load the loci list from a csv file

    Parameters:

        loci_pathname (str):	A string specifying a path to the input file

        loci (list):		    A list to be populated with loci and their coverages

    Returns:

        Nothing

    Description:

        This function adds each value from the file pointed to by loci_pathname
        onto the loci list. It appends a 0 after each locus to initialize the coverage.
    """

    with open(loci_pathname, "rt") as loci_fd:			        # open loci file

        for each_line in itertools.islice(loci_fd, 1, None): 	# for each line after header line

            loci.append( int(each_line.split(',')[0]) ) 	    # add first field to list
            loci.append( 0 )				                    # initialize coverege


def output_poscov(output_pathname, loci):
    """
    Summary:

        Output the positions and coverages to a file

    Parameters:

        output_pathname (str):	A string specifying a path to the input file

        loci (list):		    A list containing loci and their coverages

    Returns:

        Nothing

    Description:

        This function outputs the loci list to the file pointed to by
        output_pathname.
    """

    with open(output_pathname, "wt") as output_fd:	# open output in overwrite mode

        output_fd.write("position, coverage\n")		# write header

        row_count = len(loci) 			        	# grab number of entries

        each_field = 0					            # start at beginning of list

        while ( each_field < row_count ):		    # for each pair

            # write position and coverage to output file

            output_fd.write( str(loci[each_field]) + ", " +
                             str(loci[each_field+1]) + "\n" )

            each_field += 2				# next pair


def init_reads(reads_pathname, reads):
    """
    Summary:

        Load the reads list from a csv file into a dict, keeping track of duplicates

    Parameters:

        reads_pathname (str):	A string specifying a path to the input file

        reads (dict):		    A dict to populate with the reads data and occurances

    Returns:

        Nothing

    Description:

        This function loads a csv file into a dict. The record itself is used as a key and the
        value is used to store the number of occurances. The first occurance of a key sets the
        value field to 1, while subsequent occurances increments the value.
    """

    with open(reads_pathname, "rt") as reads_fd:			    # open the reads file

        num_records = 0

        for each_line in itertools.islice(reads_fd, 1, None):	# for each line after header line

            num_records += 1

            the_key = each_line.rstrip("\n")		            # strip newline char

            if the_key in reads:				                # is key present in dict?

                reads[the_key] += 1			                    # key exists, bump the repeat count

            else:
                reads[the_key] = 1			                    # new key, set count to 1

    print ( num_records, "records read" )       				# total record read
    print ( len(reads), "unique records"  )		           		# unique records stored



def process(loci, reads):
    """
    Summary:

        Process the reads against each loci, determining coverage

    Parameters:

        loci (list):	A list containing loci and no coverage (yet)

        reads (dict):	A dictionary containing reads and their occurances

    Returns:

        Nothing

    Description:

        This function walks the loci list to determine coverage of the reads. The reads keys
        contain both the start and length, with the value set to the number of times that
        record was found during the load, e.g. an example dictionary entry:

        { "158384123,150" : 9 }

    """

    loci_count  = len(loci)			                    # grab length of loci list

    each_loci = 0		                           		# start at beginning of loci list
    while ( each_loci < loci_count ):	                # loop over each locus/coverage pair

        the_locus = loci[each_loci]	                    # grab locus

        for each_key in reads:

            each_fields = each_key.split(",") 	    	# break string into fields

            start = int(each_fields[0])			        # 1st field is the start
            end = start + int(each_fields[1])		    # 2nd field is the length

            if (the_locus >= start) and (the_locus < end):	# is there coverage

                loci[each_loci+1] += reads[each_key]	# increment the coverage counter
                                                        # by the number of times that read
                                                        # appeared in the original file

        each_loci += 2						            # next loci pair


def main():
    """
    Summary:	Calculates the coverage of a set of loci from a set of reads

    Usage: 		python3 loci.py <loci input pathname> <reads input pathname> <output pathname>

    Example:	python3 loci.py data/loci.csv data/reads.csv output
    """

    loci = []				# declare empty lists for loci
    reads = {}				# declare empty dict for reads

    if ( check_args(sys.argv) == False ):	        # check cmd-line arguments
        sys.exit()			                        # exit if failure

    print ( "\nStarting run at", time.asctime() )

    print("Initializing loci list...")
    init_poscov(sys.argv[1], loci)		            # read into and initialize "loci" list

    print("Initializing reads dict...")
    init_reads(sys.argv[2], reads)		            # read into "reads" dict

    print("Processing...")
    process(loci, reads)                			# determine coverage

    print("Generating output...")
    output_poscov(sys.argv[3], loci)	            # save position and coverage to new file

    print ( "\nEnded run at", time.asctime() )

if __name__ == "__main__":
    main()
