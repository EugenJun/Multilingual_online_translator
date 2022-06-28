import requests
import argparse

from bs4 import BeautifulSoup

supported_langs = ['arabic', 'german', 'english', 'spanish', 'french',
                   'hebrew', 'japanese', 'dutch', 'polish', 'portuguese',
                   'romanian', 'russian', 'turkish']


def main():
    active = True
    while active:
        all_translations = ''
        user_language, target_language, word = get_user_input()
        if target_language not in supported_langs and target_language != 'all':
            print(f"Sorry, the program doesn't support {target_language.lower()}")
            break
        native_lang = supported_langs.pop(supported_langs.index(user_language))
        if target_language == 'all':
            for target_lang in supported_langs:
                response, status = connect_to_translator(native_lang, target_lang, word)
                if status not in [200, 404]:
                    print(f"Something wrong with your internet connection")
                    break
                elif status == 404:
                    print(f'Sorry, unable to find {word}')
                    break
                translations, sentences_example = get_translation(target_lang, response, all_langs=True)
                all_translations += f'{translations}\n' + f'{sentences_example}\n'
        else:
            response, status = connect_to_translator(native_lang, target_language, word)
            if status not in [200, 404]:
                print(f"Something wrong with your internet connection")
                break
            elif status == 404:
                print(f'Sorry, unable to find {word}')
                break
            translations, sentences_example = get_translation(target_language, response)
            all_translations += f'{translations}\n' + f'{sentences_example}\n'
        upload_to_file(all_translations, word)
        break


def get_user_input():
    parser = argparse.ArgumentParser()
    parser.add_argument('user_language', type=str)
    parser.add_argument('target_language', type=str)
    parser.add_argument('word', type=str)

    args = parser.parse_args()

    return args.user_language, args.target_language, args.word


def connect_to_translator(user_lang, target_lang, word):
    url = f'https://context.reverso.net/translation/' \
          f'{user_lang}-{target_lang}/{word.lower()}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    status = response.status_code

    return response, status


def get_translation(target_lang, response, all_langs=False):
    soup = BeautifulSoup(response.content, 'html.parser')
    reverso_translations = soup.find_all('a', {'class': 'translation'})
    sentences = soup.find('section', {'id': 'examples-content'}).find_all('span', {'class': 'text'})
    examples = ''

    if not all_langs:
        translations = '\n'.join([f'\n{target_lang.title()} Translations:',
                                  '\n'.join(
                                      [reverso_translation.get_text().strip()
                                       for reverso_translation in reverso_translations[1:6]])])

        word_examples = '\n'.join([f'\n{target_lang.title()} Examples:',
                                   '\n'.join([examples + sentence.text.strip()
                                              if sentences.index(sentence) % 2 == 0
                                              else examples + sentence.text.strip() + '\n'
                                              for sentence in sentences[:10]]).strip()])
    else:
        translations = '\n'.join([f'\n{target_lang.title()} Translations:',
                                  '\n'.join(
                                      [reverso_translation.text.strip()
                                       for reverso_translation in reverso_translations[1:2]])])

        word_examples = '\n'.join([f'\n{target_lang.title()} Example:',
                                   '\n'.join([examples + sentence.text.strip()
                                              if sentences.index(sentence) % 2 == 0
                                              else examples + sentence.text.strip() + '\n'
                                              for sentence in sentences[:2]]).strip()])
    print(translations)
    print(word_examples)

    return translations, word_examples


def upload_to_file(translations, word):
    with open(f'{word}.txt', 'w', encoding='utf-8') as file:
        file.write(translations)


if __name__ == '__main__':
    main()
