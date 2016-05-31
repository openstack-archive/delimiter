..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=========================================
Openstack Delimeter - Generation ID usage
=========================================

No blueprint, this is intended as a reference document.

Statement of intent
===================

How to resolve a problem of cross project quota management seemlessly
by ensuring that atomicity of each transaction is kept intact in a
multi-user environment.


Sequencing transactions using generation id
===========================================

- There are various ways to do locking of resources to ensure data
consistency.

- The generation id is a concept of sequencing parallel writes to a
database via multiple threads in a highly concurrent environment in such
a way that data consistency is retained.

- To a layman, generation id is just a sequencing number that ensures
that the state of the database is correctly updated in a multi-threaded
world by making sure that all clients writing to the database have a
consistent view/single view.

- The generation id concept goes in parallel with a retry mechanism to
ensure that if the generation ids don't match for a client during
updates to the DB - a retry is performed to ensure that the data is
updated on the right state of the DB.


Delimeter's use of generation id
=================================

- Two aspects - One on the producer/resource provider side and the other
on the consumer side. However, the resource provider side of the story is
NOT the responsibility of delimeter and hence it's purely left out to the
individual services.

- generation id is a generic concept that could be applied in case of
delimeter to ensure that the consumers of the quotas have a consistent
view in a highly concurrent environment.


Example usage of generation id in OpenStack Delimiter
=====================================================

<TBD>
