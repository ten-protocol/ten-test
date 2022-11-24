import string, sys

all_letters = string.ascii_letters
dict = {}

for key in range(0,4):
    dict[key]={}
    for i in range(len(all_letters)):
        dict[key][all_letters[i]] = all_letters[(i + key) % len(all_letters)]

if __name__ == "__main__":
    text = sys.argv[1]
    encrypt_txt = []
    key=0
    for char in text:
        if char in all_letters:
            temp = dict[key][char]
            encrypt_txt.append(temp)
        else:
            temp = char
            encrypt_txt.append(temp)
        key=(key+1)%4

    print("Encrypted text is:", "".join(encrypt_txt))
