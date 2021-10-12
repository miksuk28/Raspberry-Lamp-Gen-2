### FUNCTIONS AND EVERYTHING RELATED TO VALIDATION ###

def validate(keys, dict):
    '''
    Checks if keys exist in dict,
    and if they are not equal to False

    :return:    True on OK, False else
    '''
    if dict == None:
        return False

    for key in keys:
        if key in dict.keys():
            if dict[key] == "":
                return False
        else:
            return False

    return True

def within_pwm_range(numbers, pwm_range=(0, 255)):
    for number in numbers:
        if number < pwm_range[0] or number > pwm_range[1]:
            return False

    return True