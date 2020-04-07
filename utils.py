from constants import PATH_STANDARD_ANSWERS
import yaml


def read_yaml_file(path):
    with open(path, 'r') as stream:
        try:
            content_as_dict = yaml.safe_load(stream)
        except yaml.YAMLError as e:
            if VERBOSE:
                print(repr(e))
            raise(e)
    return content_as_dict


def get_standard_answers():
    standard_answers = read_yaml_file(PATH_STANDARD_ANSWERS)
    return standard_answers
