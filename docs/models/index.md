# ERD Diagram — Model Layer

This page provides an **Entity–Relationship Diagram (ERD)** of the Django model layer.

The diagram represents the project's models and the relationships between them, providing a high-level overview of the application's data structure and dependencies.

!!! note
    This diagram is generated automatically by a GitHub Actions workflow whenever changes are pushed to the repository. As a result, the diagram stays synchronized with the current Django model definitions.


## Explore the Diagram

The interactive ERD viewer provides a more convenient way to explore the model structure, inspect relationships, and navigate through the entire model graph.

<a href="erd-viewer.html" class="md-button md-button--primary">
    Open Interactive Diagram
</a>


!!! warning "First-time loading"
    The interactive diagram uses JavaScript libraries loaded from external CDNs.  
    On the first visit, please be patient while the required resources are downloaded and initialized.

    Subsequent visits may load faster once these resources are cached by your browser.


## Generation

The diagram is generated automatically from the Django project using:

* **[django-erd-generator](https://pypi.org/project/django-erd-generator/)** — extracts the Django models and their relationships.
* **[Mermaid](https://mermaid.js.org/)** — renders the generated entity–relationship diagram.
* **[GitHub Actions](https://docs.github.com/en/actions)** — regenerates the diagram as part of the project's documentation workflow.



## What the Diagram Shows

The ERD provides a visual overview of:

* Django models
* Model fields
* Primary keys
* Foreign key relationships
* One-to-one relationships
* Many-to-many relationships
* Relationships between different Django applications

It is intended as a **high-level map of the model layer** rather than a replacement for the model source code.

!!! info
    The Django model definitions are the source of truth. The ERD is a generated representation and should not be edited manually.

## Keeping the Diagram Up to Date

Because the diagram is generated as part of the documentation workflow, changes to the model layer are automatically reflected in the published diagram after the workflow completes.

This means there is no need to manually maintain a separate ERD whenever a model or relationship is added, removed, or modified.
