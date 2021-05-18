# These imports are necessary for running alembic
# with the --autogenerate flag:

# 1. Import the base Model class
from .utils.base import Model  # noqa

# 2. Import all model files
from .languages.models import *  # noqa
from .lexemes.models import *  # noqa
from .literature.models import *  # noqa
