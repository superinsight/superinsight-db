<p align="center">
  <img src='docs/media/banner.png' width='80%'>
</p>

---

Superinsight is a Relational Database for Unstructured Data.

- [What is Superinsight?](#what-is-superinsight)
- [Docs](#docs)
- [Get Started](#get-started)
- [Environment Variables](#environment-variables])
- [Need Help?](#need-help)
- [Contributing](#contributing)

## What is Superinsight?

Superinsight is a Relational Database for Unstructured Data, its main purpose is to provide a simple SQL interface to store and search unstructured data. Superinsight is build on top of PostgreSQL so you can take advantage of everything in PostgreSQL plus the ability to run machine learning operations using SQL statements.

## Docs

For guidance on how to use Superinsight, see our [User Documentation](https://docs.superinsight.ai/).

## Get Started

The best way to get started with Superinsight is to build and run our docker image
```
docker run \
--name superinsight-db-standalone \
-p 5432:5432 \
-e SUPERINSIGHT_USER=admin \
-e SUPERINSIGHT_PASSWORD=password \
superinsight/superinsight-db-standalone:latest
```

To mount a volumn to the data directory located in the path use the -v argument.
```
docker run \
--name superinsight-db-standalone \
-p 5432:5432 \
-v ~/db:/db \
-v ~/db/superinsight/logs:/db/superinsight/logs \
-v ~/db/superinsight/models:/db/superinsight/models \
-e SUPERINSIGHT_USER=admin \
-e SUPERINSIGHT_PASSWORD=password \
superinsight/superinsight-db-standalone:latest
```

## Environment Variables
Variable 					          | Usage														 	                                      | Default
--------------------------- | ------------------------------------------------------------ 	          | --------
SUPERINSIGHT_USER 			    | The username of the database super user						                      | admin
SUPERINSIGHT_PASSWORD 		  | The password of the database super user 						                    | password
ENV_IMAGE_TO_CAPTION 		    | Automatically index images to text caption for better search            | False
ENV_IMAGE_TO_LABEL 		      | Automatically index images to image labels for better search  					| False


## Need Help?

For filing bugs, suggesting improvements, or requesting new features, help us out by [opening an issue](https://github.com/superinsight/superinsight-db/issues/new).

## Contributing

Contributions to Superinsight are welcomed. If you're looking for issues to work on, try looking at the [good first issue list](https://github.com/superinsight/superinsight-db/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22). We do our best to tag issues suitable for new external contributors with that label, so it's a great way to find something you can help with!
