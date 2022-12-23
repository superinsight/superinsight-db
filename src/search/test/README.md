# Test Commands

```
ENV_STORAGE="./db" python -m unittest test.test_faiss
python -m unittest test.test_embed
ENV_IMAGE_TO_CAPTION="True" ENV_IMAGE_TO_LABEL="True" python -m unittest test.test_text_to_image
python -m unittest test.test_source_location
```
