import re


def is_valid_aws_arn(arn_string):
    """
    Validate if the given string is a valid AWS ARN.

    :param arn_string: The ARN string to be validated.
    :return: True if the ARN string is valid, otherwise False.
    """
    arn_pattern = re.compile(
        r'^arn:(backends[a-zA-Z0-9-]*):([a-zA-Z0-9-]+):([a-zA-Z0-9-]*):(\d{12}):([a-zA-Z0-9-/:\._]+)$'
    )
    return bool(arn_pattern.match(arn_string))

def transform_job_id_to_arn(job_id: str):
    """
    Transform the given job ID to an AWS ARN.

    :param job_id: The job ID to be transformed.
    :return: The transformed job ID.
    """
    return job_id.replace("_", "/")


BRAKET_NAME_SV1 = "SV1"
BRAKET_NAME_DM1 = "dm1"
BRAKET_NAME_IONQ_ARIA = "Aria 1"
BRAKET_NAME_IONQ_HARMONY = "Harmony"
BRAKET_NAME_RIGETTI_ASPEN = "Aspen-M-3"
BRAKET_NAME_OQC_LUCY = "Lucy"
