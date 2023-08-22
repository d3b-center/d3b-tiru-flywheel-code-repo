# https://flywheel-io.gitlab.io/product/backend/sdk/branches/master/python/quick_reference.html#data-model-containers

# Access Types:
# 'admin'- admin
# 'rw' - read/write
# 'ro'- read only

my_group = fw.get('group-id')

# adding user to group
access_type = 'rw'
user_id = 'example@user.com'
my_group.add_permission({'access':access_type, '_id':user_id})


# creating a new group
new_group = flywheel.Group(id='my_id', label='My Label')
my_group_id = fw.add_group(new_group)  # Returns the group id as a string
my_group = fw.get(my_group_id)