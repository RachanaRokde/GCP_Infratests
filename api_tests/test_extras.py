# import argparse
# import pytest
# import yaml
#
# parser = argparse.ArgumentParser()
# parser.add_argument("--file", required=True, help='Path to the YAML file to be read')
# args, unknown_args = parser.parse_known_args()
#
# @pytest.fixture
# def yaml_content():
#     file_path = args.file
#     with open(file_path, 'r') as file:
#         content = yaml.safe_load(file)
#         return content
#
# def test_print_file_content(yaml_content):
#     print(yaml_content)

# test_example.py

def test_with_custom_arg(request):
    custom_arg_value = request.config.getoption("--file")
    # Use custom_arg_value in your test logic
    print(custom_arg_value)