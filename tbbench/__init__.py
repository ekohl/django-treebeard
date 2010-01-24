# -*- coding: utf-8 -*-
"""

   tbbench - Lies, damn lies, and benchmarks for treebeard
   -------------------------------------------------------

   :synopsys: Benchmarks for ``treebeard``
   :copyright: 2008-2010 by Gustavo Picon
   :license: Apache License 2.0

   tbbench is a django app that isn't installed by default. I wrote it to find
   spots that could be optimized, and it may help you to tweak your database
   settings.

   To run the benchmarks:
      
      1. Add ``tbbench`` to your Python path
      2. Add ``'tbbench'`` to the ``INSTALLED_APPS`` section in your django
         settings file.
      3. Run :command:`python manage.py syncdb`
      4. In the ``tbbench`` dir, run :command:`python run.py`

   .. note::
       If the `django-mptt`_ package is also installed, both libraries will
       be tested with the exact same data and operations.

   Currently, the available tests are:

      1. Inserts: adds 1000 nodes to a tree, in different places: root
         nodes, normal nodes, leaf nodes
      2. Descendants: retrieves the full branch under every node several times.
      3. Move: moves nodes several times. This operation can be expensive
         because involves reodrering and data maintenance.
      4. Delete: Removes groups of nodes.

   For every available library (treebeard and mptt), two models are tested: a
   vanilla model, and a model with a "tree order by" attribute enabled
   (:attr:`~treebeard.MP_Node.node_order_by` in treebeard,
   ``order_insertion_by`` in mptt).

   Also, every test will be tested with and without database transactions
   (``tx``).

   The output of the script is a reST table, with the time for every test in
   milliseconds (so small numbers are better).

   By default, these tests use the default tables created by ``syncdb``. Even
   when the results of ``treebeard`` are good, they can be improved *a lot*
   with better indexing. The Materialized Path Tree approach used by
   ``treebeard`` is *very* sensitive to database indexing, so you'll
   probably want to ``EXPLAIN`` your most common queries involving the
   :attr:`~treebeard.MP_Node.path` field and add proper indexes.

   .. note::

    Tests results in Ubuntu 8.04.1 on a Thinkpad T61 with 4GB of ram.

    .. warning::

       These results shouldn't be taken as *"X is faster than Y"*,
       but as *"both X and Y are very fast"*.

    Databases tested:

     - MySQL InnoDB 5.0.51a, default settings
     - MySQL MyISAM 5.0.51a, default settings
     - PostgreSQL 8.2.7, default settings, mounted on RAM
     - PostgreSQL 8.3.3, default settings, mounted on RAM
     - SQLite3, mounted on RAM

    +-------------+--------------+-------------------+-------------------+-------------------+-------------------+-------------------+
    | Test        | Model        |       innodb      |       myisam      |        pg82       |        pg83       |       sqlite      |
    |             |              +---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    |             |              |  no tx  |    tx   |  no tx  |    tx   |  no tx  |    tx   |  no tx  |    tx   |  no tx  |    tx   |
    +=============+==============+=========+=========+=========+=========+=========+=========+=========+=========+=========+=========+
    | Inserts     | TB MP        |    3220 |    2660 |    3181 |    2766 |    2859 |    2542 |    2540 |    2309 |    2205 |    1934 |
    |             +--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    |             | TB AL        |    1963 |    1905 |    1998 |    1936 |    1937 |    1775 |    1736 |    1631 |    1583 |    1457 |
    |             +--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    |             | TB NS        |    3386 |    3438 |    3359 |    3420 |    4061 |    7242 |    3536 |    4401 |    2794 |    2554 |
    |             +--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    |             | MPTT         |    7559 |    9280 |    7525 |    9028 |    5202 |   14969 |    4764 |    6022 |    3781 |    3484 |
    |             +--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    |             | TB MP Sorted |    4732 |    5627 |    5038 |    5215 |    4022 |    4808 |    3415 |    3942 |    3250 |    3045 |
    |             +--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    |             | TB AL Sorted |    1096 |    1052 |    1092 |    1033 |    1239 |     999 |    1049 |     896 |     860 |     705 |
    |             +--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    |             | TB NS Sorted |    6637 |    6373 |    6283 |    6313 |    7548 |   10053 |    6717 |   10941 |    5907 |    5461 |
    |             +--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    |             | MPTT Sorted  |    8564 |   10729 |    7947 |   10221 |    6077 |    7567 |    5490 |    6894 |    4842 |    4284 |
    +-------------+--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    | Descendants | TB MP        |    6298 |     N/A |    6460 |     N/A |    7643 |     N/A |    7132 |     N/A |   10415 |     N/A |
    |             +--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    |             | TB AL        |   56850 |     N/A |  116550 |     N/A |   54249 |     N/A |   50682 |     N/A |   50521 |     N/A |
    |             +--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    |             | TB NS        |    5595 |     N/A |    5824 |     N/A |   10080 |     N/A |    5840 |     N/A |    5965 |     N/A |
    |             +--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    |             | MPTT         |    5268 |     N/A |    5306 |     N/A |    9394 |     N/A |    8745 |     N/A |    5197 |     N/A |
    |             +--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    |             | TB MP Sorted |    6698 |     N/A |    6408 |     N/A |    8248 |     N/A |    7265 |     N/A |   10513 |     N/A |
    |             +--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    |             | TB AL Sorted |   59817 |     N/A |   59718 |     N/A |   56767 |     N/A |   52574 |     N/A |   53458 |     N/A |
    |             +--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    |             | TB NS Sorted |    5631 |     N/A |    5858 |     N/A |    9980 |     N/A |    9210 |     N/A |    6026 |     N/A |
    |             +--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    |             | MPTT Sorted  |    5186 |     N/A |    5453 |     N/A |    9723 |     N/A |    8912 |     N/A |    5333 |     N/A |
    +-------------+--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    | Move        | TB MP        |     837 |    1156 |     992 |    1211 |     745 |    1040 |     603 |     740 |     497 |     468 |
    |             +--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    |             | TB AL        |    8708 |    8684 |    9798 |    8890 |    7243 |    7213 |    6721 |    6757 |    7051 |    6863 |
    |             +--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    |             | TB NS        |     683 |     658 |     660 |     679 |    1266 |    2000 |     650 |     907 |     672 |     637 |
    |             +--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    |             | MPTT         |    6449 |    7793 |    6356 |    7003 |    4993 |   20743 |    4445 |    8977 |     921 |     896 |
    |             +--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    |             | TB MP Sorted |    6730 |    7036 |    6743 |    7023 |    6410 |   19294 |    3622 |   12380 |    2622 |    2487 |
    |             +--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    |             | TB AL Sorted |    3866 |    3731 |    3873 |    3717 |    3587 |    3599 |    3394 |    3371 |    3491 |    3416 |
    |             +--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    |             | TB NS Sorted |    2017 |    2017 |    1958 |    2078 |    4397 |    7981 |    3892 |    8110 |    1543 |    1496 |
    |             +--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    |             | MPTT Sorted  |    6563 |   10540 |    6427 |    9358 |    5132 |   20426 |    4601 |    9428 |     957 |     955 |
    +-------------+--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    | Delete      | TB MP        |     714 |     651 |     733 |     686 |     699 |     689 |     595 |     561 |     636 |     557 |
    |             +--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    |             | TB AL        |     975 |    1093 |    2199 |     991 |     758 |     847 |     714 |     804 |     843 |     921 |
    |             +--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    |             | TB NS        |     745 |     745 |     742 |     763 |     555 |     698 |     430 |     506 |     530 |     513 |
    |             +--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    |             | MPTT         |    2928 |    4473 |    2914 |    4814 |   69385 |  167777 |   18186 |   26270 |    1617 |    1635 |
    |             +--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    |             | TB MP Sorted |     811 |     751 |     808 |     737 |     798 |    1180 |     648 |    1101 |     612 |     565 |
    |             +--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    |             | TB AL Sorted |    1030 |    1030 |    1055 |     987 |     797 |    1023 |     760 |     969 |     884 |     859 |
    |             +--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    |             | TB NS Sorted |     756 |     750 |     728 |     758 |     807 |     847 |     576 |     748 |     501 |     490 |
    |             +--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+
    |             | MPTT Sorted  |    3729 |    5108 |    3833 |    4776 |   86545 |  148596 |   34059 |  127125 |    2024 |    1787 |
    +-------------+--------------+---------+---------+---------+---------+---------+---------+---------+---------+---------+---------+


   .. _`django-mptt`: http://code.google.com/p/django-mptt/

"""

