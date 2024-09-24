def remove_module(module_name, requirements_file='requirements.txt'):
    with open(requirements_file, 'r') as file:
        lines = file.readlines()

    module_found = False
    with open(requirements_file, 'w') as file:
        for line in lines:
            if line.startswith(module_name):
                module_found = True
            else:
                file.write(line)

    if not module_found:
        print(f"Module {module_name} not found in {requirements_file}")

if __name__ == "__main__":
    module_name = 'opencv-python==4.10.0.84'
    remove_module(module_name)
