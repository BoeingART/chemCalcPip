import argparse
import os
from pathlib import Path
import re


def parser_data():
    """Used to collect the CUI parsers.

    Returns:
        <namespace>
    """
    data = argparse.ArgumentParser(
        prog="gaussian to multiwfn calculation",
        usage="used to get gview file and translate to standard gaussian input file."
    )

    data.add_argument("files", nargs="+", help="add your file path and name.")
    data.add_argument("-c", "--calculate", dest="calculate",
                      action="store_false", help="choose whether or not to calculate. default calculate.")
    data.add_argument("-m", "--method", dest="method",
                      default="b3lyp", help="choose your method.")
    data.add_argument("-b", "--base-set", dest="base_set",
                      default="6-31g*", help="choose your base set.")
    data.add_argument("-o", "--output-format", dest="output_format",
                      default="out", help="choose the form of the output file.")
    data.add_argument("-s", "--save-chk", dest="save", action="store_false",
                      help="choose whether to save the .chk file. default saves.")
    data.add_argument("-v", "--view", dest="view", action="store_false",
                      help="choose to output the calculation on the screen. default views.")
    data.add_argument("-f", "--functions", dest="functions",
                      nargs="*", help="add your personal missions.")

    return data.parse_args()


if __name__ == "__main__":
    settings = Path(__file__).parent / Path("settings.ini")
    out = parser_data()
    print(out)
    functions = ""
    if out.functions != None:
        for i in out.functions:
            functions += (i + " ")

    input_files = []
    for file in out.files:
        if file.endswith(".gjf"):
            input_files.append(file)

    # file check
    for file in input_files:
        try:
            Path(file).exists() == True
        except:
            print("there is no file: {}".format(file))
            exit(1)

    # read file

    for file in input_files:
        parts = {"settings": "", "title": "", "molecule": ""}
        os.system("cp {} {}_backup.gjf".format(str(Path(file)), str(Path(file).parent / Path(file).stem)))
        file = Path(file).resolve()
        file_path = file.parent
        file_name = file.stem
        
        input = file.read_text()
        content = input.split("\n\n")
        while content[-1] == "" or content[-1] == "\n":
            content.pop()

        for part in content:
            try:
                assert part != ""
            except:
                print("input format error. please check your input file.")

        for i in range(0, 9):
            if re.match(" {}".format(i), content[-1]) != None:
                content.pop()
                break

        content[0] = (settings).read_text()
        if out.save:
            content[0] += "%chk={}.chk\n".format(
                str(file.parent / file.stem))
        content[0] += "#p {} {} {}".format(out.method,
                                            out.base_set, functions)

        with open(file, "w") as output:
            for i in content:
                output.write(i + "\n\n")
            output.write("\n\n\n")

    if out.calculate:
        try:
            if out.view:
                for i in range(len(input_files)):
                    os.system("g16 < {} | tee {}".format(
                        input_files[i], os.path.split(input_files[i])[1].split(".")[0] + ".out"))
            else:
                for i in range(len(input_files)):
                    os.system("g16 < {} > {}".format(input_files[i], os.path.split(
                        input_files[i])[1].split(".")[0] + ".out"))
            os.system("rm {}_backup.gjf".format(str(Path(file).parent / Path(file).stem)))
        except Exception as e:
            print("calculation Wrong! {}".format(e))
            
        
