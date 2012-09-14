#!/usr/bin/env python

from cogent.app.util import CommandLineApplication,\
    CommandLineAppResult, ResultPath
from cogent.app.parameters import Parameter, FlagParameter, ValuedParameter,\
    MixedParameter,Parameters, _find_synonym
from cogent.core.alignment import Alignment
from cogent.core.moltype import RNA
from cogent.parse.fasta import MinimalFastaParser
from cogent.parse.rnaalifold import rnaalifold_parser, MinimalRnaalifoldParser
from cogent.format.clustal import clustal_from_alignment
from cogent.struct.rna2d import ViennaStructure

__author__ = "Shandy Wikman"
__copyright__ = "Copyright 2007-2012, The Cogent Project"
__contributors__ = ["Shandy Wikman","Jeremy Widmann"]
__license__ = "GPL"
__version__ = "1.5.3-dev"
__maintainer__ = "Shandy Wikman"
__email__ = "ens01svn@cs.umu.se"
__status__ = "Development"

class RNAalifold(CommandLineApplication):
    """Application controller for RNAalifold application

    reads aligned RNA sequences from stdin or file.aln and calculates
    their minimum free energy (mfe) structure,  partition  function
    (pf)  and  base pairing probability matrix.

OPTIONS
       -cv <float>
              Set  the weight of the covariance term in the energy function to
              factor. Default is 1.


       -nc <float>
              Set the penalty for non-compatible sequences in  the  covariance
              term of the energy function to factor. Default is 1.

       -E     Score pairs with endgaps same as gap-gap pairs.

       -mis   Output \"most informative sequence\" instead of simple consensus:
              For each column of the alignment output the set  of  nucleotides
              with frequence greater than average in IUPAC notation.

       -p     Calculate  the  partition  function and base pairing probability
              matrix in addition to the mfe structure. Default is  calculation
              of mfe structure only.

       -noLP  Avoid  structures without lonely pairs (helices of length 1). In
              the mfe case structures with lonely pairs are  strictly  forbid-
              den.  For  partition  function folding this disallows pairs that
              can only occur isolated.  Setting this option provides a signif-
              icant speedup.

       The -T, -d, -4, -noGU, -noCloseGU, -e, -P, -nsp, options should work as
       in RNAfold

       If using -C constraints will be read from stdin, the alignment  has  to
       given as a filename on the command line.

       For more info see respective man pages. 

    """


    _parameters = {
        '-cv':ValuedParameter(Prefix='-',Name='cv',Delimiter=' '),
        '-nc':ValuedParameter(Prefix='-',Name='nc',Delimiter=' '),
        '-E':FlagParameter(Prefix='-',Name='E'),
        '-mis':FlagParameter(Prefix='-',Name='mis'),
        '-noLP':FlagParameter(Prefix='-',Name='noLP'),
        '-T':ValuedParameter(Prefix='-',Name='T',Value=37,Delimiter=' '),
        '-4':FlagParameter(Prefix='-',Name=4),
        '-d':MixedParameter(Prefix='-',Name='d',Delimiter=''),
        '-noGU':FlagParameter(Prefix='-',Name='noGU'),
        '-noCloseGU':FlagParameter(Prefix='-',Name='noCloseGU'),
        '-e':ValuedParameter(Prefix='-',Name='e',Delimiter=' '),
        '-P':ValuedParameter(Prefix='-',Name='P',Delimiter=' '),
        '-nsp':ValuedParameter(Prefix='-',Name='nsp',Delimiter=' '),
        '-C':FlagParameter(Prefix='-',Name='C')}
    
    _synonyms = {'Temperature':'-T','Temp':'-T','EnergyRange':'-e'}

        
    _command = 'RNAalifold'
    _input_handler = '_input_as_string'

    def _get_result_paths(self, data):
        """Specify the paths of the output files generated by the application

        You always get back: StdOut, StdErr, and ExitStatus.
        In addition RNAalifold writes a file: alirna.ps. It seems that this
            file is always written (no exceptions found so far.
        The documentation says the application can produce a dotplot
            (alidot.ps), but it is unclear when this file is produced, and
            thus it is not added to the results dictionary.
        """
        
        result = {}

        result['SS'] = ResultPath(Path=self.WorkingDir+'alirna.ps',\
            IsWritten=True)

        return result

def rnaalifold_from_alignment(aln,moltype=RNA,params=None):
    """Returns seq, pairs, folding energy for alignment.
    """
    #Create Alignment object.  Object will handle if seqs are unaligned.
    aln = Alignment(aln,MolType=RNA)
    int_map, int_keys = aln.getIntMap()

    app = RNAalifold(WorkingDir='/tmp',\
        InputHandler='_input_as_multiline_string',params=params)
    res = app(clustal_from_alignment(int_map))
    
    #seq,pairs,energy = rnaalifold_parser(res['StdOut'].readlines())
    pairs_list = MinimalRnaalifoldParser(res['StdOut'].readlines())

    res.cleanUp()
    return pairs_list

if __name__ == "__main__":
    from sys import argv
    aln_file = argv[1]
    aln = dict(MinimalFastaParser(open(aln_file,'U')))
    res = rnaalifold_from_alignment(aln)
    print res
    
    
