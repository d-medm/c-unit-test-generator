import os
from typing import Tuple 
import yaml
import subprocess

def load_instructions(yaml_path: str):
    # load yaml instruction files
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    return "\n".join(data['instructions'])

#======== Generate initial tests ========

#read all c++ files (.cpp or .h) from src folder
def read_cpp_files(source_dir: str):
    cpp_files = []
    for root, _, files in os.walk(source_dir):
        for file in files:
            # make sure they end in .cpp or .h
            if file.endswith('.cpp') or file.endswith('.h'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    code = f.read()
                cpp_files.append((file, code))
    return cpp_files

def query_llm(prompt: str, model: str) -> str:
    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=300
    )
    if result.returncode != 0:
        print("LLM error:", result.stderr.decode())
        return ""
    return result.stdout.decode()

def generate_tests_for_file(instruction: str, filename: str, code: str, model: str) -> str:
    # create a prompt 
    prompt = f"""{instruction}
        FILE: {filename}
        CODE: {code}
        
        PROVIDE GOOGLE TEST CODE. 
        DO NOT INCLUDE FORMATTING."""
    return query_llm(prompt, model)

def save_test_file(output_dir, source_filename, test_code):
    # sometimes output includes markdown format, 
    # this makes sure to remove it from output
    test_code = test_code.replace("```ccp", "").strip()

    # create test file
    test_filename = source_filename.replace('.cpp', '_test.cpp').replace('.h', '_test.cpp')
    
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, test_filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(test_code)
    print(f"Saved test to {filepath}")


# ========== Refinement ============
def read_generated_tests(test_dir: str):
    test_files = []
    for root, _, files in os.walk(test_dir):
        for file in files:
            if file.endswith('_test.cpp'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    code = f.read()
                test_files.append((file, code))
    return test_files

# refine the tests
def refine_test_files(refine_instructions: str, original_source: str, test_code: str, model: str):
    # create a prompt
    prompt = f"""{refine_instructions}

    ORIGINAL SOURCE CODE: {original_source}

    GENERATED TEST CODE TO REFINE: {test_code}

    PROVIDE REFINED GOOGLE TEST CODE.
    DO NOT INCLUDE FORMATTING. """

    return query_llm(prompt, model)

# save refined tests to new file
def save_refined_tests(output_dir: str, filename: str, refined_code: str):
    # also remove markdown format from refined tests
    refined_code = refined_code.replace("```", "").strip()

    #create new test files
    refined_filename = filename.replace('_test.cpp', '_test_refined.cpp')
    
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, refined_filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(refined_code)
    print(f"Saved refined test to {filepath}")

# ======== Test Build =======
def fix_tests(build_instructions: str, test_code: str, log: str, model: str):
    prompt = f"""{build_instructions}

    FAILING TEST CODE: {test_code}

    BUILD ERROR LOG: {log}

    PROVIDE FIXED GOOGLE TEST CODE.
    DO NOT INCLUDE FORMATTING."""

    return query_llm(prompt, model)

def build() -> Tuple[bool, str]:
    # Create build directory
    os.makedirs("build", exist_ok=True)
    
    # get all test files and source files
    test_files = []
    source_files = []
    
    # get all test files
    if os.path.exists("output/tests"):
        for file in os.listdir("output/tests"):
            if file.endswith('_test_refined.cpp'):
                test_files.append(os.path.join("output/tests", file))
            elif file.endswith('_test.cpp') and not any('_refined' in tf for tf in test_files):
                test_files.append(os.path.join("output/tests", file))
    
    # get all source files
    if os.path.exists("src"):
        for file in os.listdir("src"):
            if file.endswith('.cpp') or file.endswith('.h'):
                source_files.append(os.path.join("src", file))
    
    if not test_files:
        return False, "No test files found"
    
    # build command
    cmd = [
        "g++", "-std=c++17",
        "-I", "src",  # include source directory
        "--coverage",  # enable coverage
        "-g", "-O0",   # debug info
        "-fprofile-arcs", "-ftest-coverage",  # coverage flags
        "-lgtest", "-lgtest_main", "-lpthread"
    ]
    cmd.extend(test_files)
    cmd.extend(source_files)
    cmd.extend(["-o", "build/test_executable"])
    
    print(f"Building with command: {' '.join(cmd)}")
    
    proc = subprocess.run(cmd, capture_output=True, text=True)
    
    if proc.returncode != 0:
        return False, proc.stderr + proc.stdout
    
    # if build succeeded, try to run the tests
    test_run = subprocess.run(
        ["./build/test_executable"], 
        capture_output=True, text=True
    )
    
    if test_run.returncode != 0:
        return False, f"Tests failed to run:\n{test_run.stderr + test_run.stdout}"
    
    return True, test_run.stdout

def generate_coverage_report() -> Tuple[bool, str]:
    """Generate coverage report using gcov."""
    try:
        # generate coverage data
        subprocess.run(["gcov", "-r", "src/*.cpp"], cwd="build", capture_output=True)
        
        # try to use lcov if available
        try:
            # create coverage info
            subprocess.run([
                "lcov", "--capture", "--directory", "build",
                "--output-file", "build/coverage.info"
            ], check=True, capture_output=True)
            
            # generate HTML report
            subprocess.run([
                "genhtml", "build/coverage.info",
                "--output-directory", "build/coverage_html"
            ], check=True, capture_output=True)
            
            return True, "Coverage report generated in build/coverage_html"
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fall back to basic gcov
            coverage_files = []
            if os.path.exists("build"):
                for file in os.listdir("build"):
                    if file.endswith(".gcov"):
                        coverage_files.append(file)
            
            if coverage_files:
                return True, f"Basic coverage files generated: {coverage_files}"
            else:
                return False, "No coverage files found"
                
    except Exception as e:
        return False, f"Coverage generation failed: {e}"

def main():
    print("\n======== GENERATING TESTS ========")
    # load instructions and model
    instructions = load_instructions('prompts/initial.yaml')
    model = "codellama:7b"

    # read source files
    cpp_files = read_cpp_files('src')

    source_code_map = {}

    # generate and save original tests
    for filename, code in cpp_files:
        print(f"Generating tests for {filename}...")
        source_code_map[filename] = code
        test_code = generate_tests_for_file(instructions, filename, code, model)
        if test_code:
            save_test_file('output/tests', filename, test_code)
        else:
            print(f"Failed to generate tests for {filename}")
    print("======== TESTS GENERATED ========")

    # ============ refined tests ===========
    print("\n======== REFINING TESTS ========")

    refinement_instructions = load_instructions('prompts/refine.yaml')

    # read generated tests
    generated_tests = read_generated_tests('output/tests')

    # refine and save refined tests
    for filename, test_code in generated_tests:
        print(f"Refining tests for {filename}...")

        # Find corresponding source file
        source_filename = filename.replace('_test.cpp', '.cpp')
        if source_filename not in source_code_map:
            source_filename = filename.replace('_test.cpp', '.h')
        
        original_source = source_code_map.get(source_filename, "")
        refined_code = refine_test_files(refinement_instructions, original_source, test_code, model)

        refined_code = refine_test_files(refinement_instructions, original_source, test_code, model)
        if refined_code:
            save_refined_tests('output/tests', filename, refined_code)
        else:
            print(f"Failed to refine tests for {filename}")

    print("======== REFINEMENT COMPLETE ========")

    # ============ Build and Test ===========
    print("\n======== BUILDING AND TESTING ========")
    
    # build all tests together
    success, log = build()
    if not success:
        print(f"Build failed:\n{log}")
        
        # try to fix build errors
        print("\n======== ATTEMPTING TO FIX BUILD ERRORS ========")
        build_instructions = load_instructions('prompts/fix_build.yaml')
        
        # read all test files to potentially fix
        refined_tests = [(f, c) for f, c in read_generated_tests('output/tests') if '_refined' in f]
        
        for filename, test_code in refined_tests:
            print(f"Attempting to fix {filename}...")
            fixed_code = fix_tests(build_instructions, test_code, log, model)
            
            if fixed_code:
                fixed_filename = filename.replace('_refined.cpp', '_fixed.cpp')
                save_test_file('output/tests', fixed_filename, fixed_code)
                print(f"Saved fixed test: {fixed_filename}")
        
        # retry build
        print("Retrying build with fixed tests...")
        success, log = build()
        
    if success:
        print("BUILD SUCCESSFUL!")
        print("Test output:", log)

        # generate coverage report
        print("\n======== STEP 4: GENERATING COVERAGE REPORT ========")
        coverage_success, coverage_info = generate_coverage_report()
        
        if coverage_success:
            print("Coverage report generated successfully!")
            print(coverage_info)
        
        else:
            print(f"Coverage generation failed: {coverage_info}")
    else:
        print(f"Build still failed:\n{log}")

    print("\n======== BUILD AND TEST COMPLETE ========")


if __name__ == "__main__":
    main()
