#imports
import unittest
from openmsipython.shared.argument_parsing import OpenMSIPythonArgumentParser

class TestArgumentParsing(unittest.TestCase) :
    """
    Class for testing functions in shared/argument_parsing.py
    """

    #test MyArgumentParser by just adding a bunch of arguments
    def test_my_argument_parser(self) :
        parser = OpenMSIPythonArgumentParser()
        parser.add_arguments('pdv_plot_type')
        args = ['--pdv_plot_type','spall']
        args = parser.parse_args(args=args)
        self.assertEqual(args.pdv_plot_type,'spall')
        with self.assertRaises(ValueError) :
            parser = OpenMSIPythonArgumentParser()
            parser.add_arguments('never_name_a_command_line_arg_this')
