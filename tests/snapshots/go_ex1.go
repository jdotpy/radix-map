package main

type User struct {
    Name string
}

func (u *User) GetName() string {
    return u.Name
}

func internalHelper() {
    // private
}