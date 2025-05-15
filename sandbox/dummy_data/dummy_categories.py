from .abstraction import *
from catalogue.models import Category


class DummyCategoryHandler(AbstractHandler):
    def __init__(self, roots=2, depth=4):
        self.tree_depth = depth
        self.tree_roots = roots
        self.faker = Faker()
        self.tree = list()

    def handle(self, flag, **kwargs):
        if flag:
            self.create_tree()
            self.logger.info("Dummy category tree created and saved to database.")
        return super().handle(flag, **kwargs)

    def data(self):
        slug = self.faker.unique.word().capitalize()
        name = slug + " " + self.faker.word().capitalize()
        background_caption = self.faker.text(max_nb_chars=128)
        is_public = random.choices([True, False], weights=[90, 10])[0]
        ancestors_are_public = random.choices([True, False], weights=[95, 5])[0]
        meta_title = self.faker.catch_phrase()
        meta_description = self.faker.text(max_nb_chars=300)

        return {
            "data": {
                "name": name,
                "slug": slug,
                "is_public": is_public,
                "ancestors_are_public": ancestors_are_public,
                "background_caption": background_caption,
                "meta_title": meta_title,
                "meta_description": meta_description,
                "description": meta_description
            }
        }

    def create_tree(self):
        for _ in range(self.tree_roots):
            node = self.data()
            self.tree.append(node)

        current_nodes = self.tree

        for layer in range(self.tree_depth - 1):
            new_nodes = list()
            for node in current_nodes:
                new = self.create_child_nodes()
                node["children"] = new
                new_nodes += new
            current_nodes = new_nodes

        self.save()

    def save(self):
        Category.load_bulk(self.tree)

    def create_child_nodes(self, numchild=2):
        children = list()
        for _ in range(numchild):
            node = self.data()
            children.append(node)
        return children
