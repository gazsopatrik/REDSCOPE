import re


class CommandPolicyError(Exception):
    pass


class CommandPolicy:
    PORT_LIST_REGEX = re.compile(r"^[0-9,-]+$")

    @classmethod
    def validate_port_list(cls, port_str: str) -> str:
        """
        Validates custom port input string. Allows numbers, commas, and hyphens (e.g. 22,80,443,8000-8080).
        Rejects shell metacharacters, spaces, or illegal strings.
        """
        clean_str = port_str.strip().replace(" ", "")
        if not clean_str:
            raise CommandPolicyError("Port specification cannot be empty.")

        if not cls.PORT_LIST_REGEX.match(clean_str):
            raise CommandPolicyError(
                f"Invalid port specification '{port_str}'. Only numbers, commas, and hyphens are allowed."
            )

        # Validate range values 1-65535
        parts = clean_str.split(",")
        for part in parts:
            if "-" in part:
                subparts = part.split("-")
                if len(subparts) != 2:
                    raise CommandPolicyError(f"Invalid port range '{part}'.")
                p1, p2 = int(subparts[0]), int(subparts[1])
                if not (1 <= p1 <= 65535 and 1 <= p2 <= 65535 and p1 <= p2):
                    raise CommandPolicyError(f"Port range '{part}' out of bounds (1-65535).")
            else:
                p = int(part)
                if not (1 <= p <= 65535):
                    raise CommandPolicyError(f"Port number '{p}' out of bounds (1-65535).")

        return clean_str
