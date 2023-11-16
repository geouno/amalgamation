# /bin/bash

./amalgamation.py -S test/arc.h -T test/test_result.hpp -I test/include -N no_expand.hpp --verbose
diff --color test/expected.hpp test/test_result.hpp

return 0
