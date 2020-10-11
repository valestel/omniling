import languagemodel
import os


def accuracy_report(language, sample, accuracy, mismatches):
    with open('accuracy_reports/' + language + '_report.txt', 'a', encoding='utf8') as report:
        text = (
            f'Test data: {sample}\n'
            f'Accuracy: {accuracy:.2f}\n'
            f'Items erroneously recognised as: {mismatches}\n'
        )
        report.write(text)


def accuracy_test(filepath, true_language):
    accuracy = 0
    mismatches = {}
    with open(filepath, 'r', encoding='utf8') as inp:
        for line in inp:
            detected = languagemodel.detect_language(line)[0][1]
            if detected == true_language:
                accuracy += 0.1
            else:
                if detected in mismatches:
                    mismatches[detected] += 0.1
                else:
                    mismatches[detected] = 0.1
    return accuracy, mismatches


for lang_dir in os.listdir('accuracy_tests'):
    if os.path.isdir(lang_dir):
        for file in os.listdir(os.path.join('accuracy_tests', lang_dir)):
            test_sample = file[:-4]
            accuracy_res, mismatches_res = accuracy_test(os.path.join('accuracy_tests', lang_dir, file), lang_dir)
            accuracy_report(lang_dir, test_sample, accuracy_res, mismatches_res)
