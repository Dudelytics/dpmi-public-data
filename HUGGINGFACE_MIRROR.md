# Public Hugging Face mirror

Target: https://huggingface.co/datasets/Dudelytics/dpmi-public-data

The canonical source remains this GitHub archive. `huggingface-mirror.yml`
runs after a successful `Daily public derived snapshot` workflow, daily at
01:30 UTC as a retry, and on manual dispatch. GitHub schedules may be delayed.

Activation requires a GitHub Actions repository secret named `HF_TOKEN`.
Use a Hugging Face fine-grained token with read/write access limited to
the target dataset. Enter it directly in GitHub Settings → Secrets and
variables → Actions; never commit it or paste it into a chat.
After adding the secret, manually run `Mirror public archive to Hugging Face`
from the Actions tab. Activation is only confirmed after a successful run.

Only the six allowlisted JSON files in complete dated `data/YYYY-MM-DD/`
directories are mirrored. Every committed file is checked against the
existing public projection functions and exact allowed fields. Unknown
fields, nonfinite numbers, partial dates, and unexpected sources block
the entire upload. No live endpoints or CoinGecko data are fetched.

Files are copied byte-for-byte from the checked-out Git commit. Existing
Hugging Face data must match exactly; differing history blocks the run.
No historical data is overwritten or deleted. Existing dataset card,
license and documentation remain unchanged. Missing files are added in
one commit with the canonical GitHub revision in its description. Newly
uploaded files are downloaded at that revision and compared byte-for-byte.
Concurrent target edits are protected by `parent_commit`.

Offline validation: `python mirror_huggingface.py --check-only`
and `python -m unittest test_mirror_huggingface.py`.

Hub client: `huggingface_hub==1.32.0`.
