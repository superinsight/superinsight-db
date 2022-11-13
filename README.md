

Superinsight is a Machine Learning Relational Database for AI applications.

- [What is Superinsight?](#what-is-superinsight)
- [Docs](#docs)
- [Get Started](#get-started)
- [Need Help?](#need-help)
- [Contributing](#contributing)

## What is Superinsight?

Superinsight is a Machine Learning Relational Database, its main purpose is to provide machine learning features within the database so any applications and business intelligence software that utliize SQL can take advantage of AI capabilities. Superinsight is build on top of PostgreSQL so you can take advantage of everything in PostgreSQL plus the ability to run machine learning operations using SQL statements.

## Docs

For guidance on how to use Superinsight, see our [User Documentation](https://docs.superinsight.ai/).

## Get Started

The best way to get started with Superinsight is to build and run our docker image
```
docker run --name superinsight-db -p 5432:5432 -e SUPERINSIGHT_USER=admin -e SUPERINSIGHT_PASSWORD=password superinsight/superinsight-db-standalone:latest
```

## Need Help?

For filing bugs, suggesting improvements, or requesting new features, help us out by [opening an issue](https://github.com/superinsight/superinsight-db/issues/new).

## Contributing

Contributions to Superinsight are welcomed. If you're looking for issues to work on, try looking at the [good first issue list](https://github.com/superinsight/superinsight-db/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22). We do our best to tag issues suitable for new external contributors with that label, so it's a great way to find something you can help with!
