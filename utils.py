def calculate_nfe_check_digit(acess_key_43: str) -> str | None:
    if len(acess_key_43) != 43:
        return None

    weights = [2, 3, 4, 5, 6, 7, 8, 9]
    total_sum = 0
    
    for i, digit in enumerate(acess_key_43[::-1]):
        weight = weights[i % 8]
        total_sum += int(digit) * weight

    remainder = total_sum % 11
    check_digit = 11 - remainder

    if check_digit >= 10:
        check_digit = 0
        
    return str(check_digit)

def get_new_acess_keys(acess_key: str, k: int = 1, n: int = 20) -> list[str]:
    ACESS_KEY_WITHOUT_CD = acess_key[:-1]

    cnf = ACESS_KEY_WITHOUT_CD[-8:]
    nnf = ACESS_KEY_WITHOUT_CD[-18:-9]
    tp_emis = ACESS_KEY_WITHOUT_CD[-9]

    new_acess_keys = []
    for i in range(1, n + 1):
        new_cnf = str(int(cnf) + i * k).zfill(8)
        new_nnf = str(int(nnf) + i * k).zfill(9)

        new_acess_key = ACESS_KEY_WITHOUT_CD[:-18] + new_nnf + tp_emis + new_cnf

        cd = calculate_nfe_check_digit(new_acess_key)

        if cd is not None:
            new_acess_keys.append(new_acess_key + cd)
        else:
            raise ValueError("Erro ao calcular o dígito verificador.")

    return new_acess_keys