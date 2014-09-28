from ..app.models import Project, Task
from .models import Links

from ..base import TestCase


class LinksTests(TestCase):

    def setUp(self):
        self.project = Project.objects.create()
        self.links = Links.objects.create()

    def test_related_accessor(self):
        self.links.related_objects.add(self.project)
        self.links.save()
        self.assertEqual(self.project.links_set.count(), 1)
        self.assertIn(self.links, self.project.links_set.all())

    def test_add_relation(self):
        """
        Adds a reverse relation to a GM2MField after an object has been added
        """
        task = Task.objects.create()
        self.links.related_objects.add(task)
        Links.related_objects.add_relation(Task)
        self.assertEqual(task.links_set.count(), 1)
        self.assertIn(self.links, task.links_set.all())


class DeletionTests(TestCase):

    def setUp(self):
        self.project1 = Project.objects.create()
        self.project2 = Project.objects.create()
        self.links = Links.objects.create()

    def test_delete_src(self):
        self.links.related_objects = [self.project1, self.project2]
        self.links.save()
        self.links.delete()
        self.assertEqual(self.project1.links_set.count(), 0)
        self.assertEqual(self.project2.links_set.count(), 0)

    def test_delete_tgt(self):
        self.links.related_objects = [self.project1, self.project2]
        self.links.save()
        self.project2.delete()
        self.assertEqual(self.links.related_objects.count(), 1)


class PrefetchTests(TestCase):

    def setUp(self):
        self.project = Project.objects.create()
        self.task = Task.objects.create()
        self.links1 = Links.objects.create()
        self.links2 = Links.objects.create()

        self.links1.related_objects = [self.project, self.task]
        self.links1.save()

        self.links2.related_objects = [self.project]
        self.links2.save()

    def test_prefetch_forward(self):
        with self.assertNumQueries(4):
            # 4 queries = 2 queries to retrieve the through models +
            # one query for each related model type (Project, Task)
            # without prefetching it takes 6 queries
            prefetched = [list(l.related_objects.all()) for l
                          in Links.objects.prefetch_related('related_objects')]

        # without prefetching, we indeed have 6 queries instead of 4
        normal = [list(l.related_objects.all())
                        for l in Links.objects.all()]

        self.assertListEqual(prefetched, normal)

    def test_prefetch_reverse(self):
        with self.assertNumQueries(2):
            # much more efficient this way as there are no supplementary
            # queries due to the generic foreign key
            prefetched = [list(p.links_set.all()) for p
                          in Project.objects.prefetch_related('links_set')]

        normal = [list(p.links_set.all()) for p in Project.objects.all()]
        self.assertEqual(prefetched, normal)