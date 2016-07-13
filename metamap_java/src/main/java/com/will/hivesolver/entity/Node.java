package com.will.hivesolver.entity;

import java.util.HashSet;
import java.util.Set;

public class Node implements Comparable<Node> {
    private Set<Node> children = new HashSet<Node>();
//    private Set<Node> parent = new HashSet<Node>();
    private boolean isCurrent;
    private String name;
    private int level = 0;
    private int schedulePriority;
    public boolean isCurrent() {
        return isCurrent;
    }
    public void setCurrent(boolean isCurrent) {
        this.isCurrent = isCurrent;
    }
    public String getName() {
        return name;
    }
    public void setName(String name) {
        this.name = name;
    }
    public int getLevel() {
        return level;
    }
    public void setLevel(int level) {
        this.level = level;
    }
    @Override
    public int compareTo(Node o) {
        return o.getLevel() - this.getLevel() ;
    }

//    public boolean addParent(Node parent) {
//        return this.getParent().save(parent);
//    }
    
    public boolean addChild(Node child) {
        if (child.getSchedulePriority() > this.schedulePriority) {
            this.schedulePriority = child.getSchedulePriority();
        }
        return this.getChildren().add(child);
    }
    public Set<Node> getChildren() {
        return children;
    }
    public void setChildren(Set<Node> children) {
        this.children = children;
    }
//    public Set<Node> getParent() {
//        return parent;
//    }
//    public void setParent(Set<Node> parent) {
//        this.parent = parent;
//    }
//    
    public int getSchedulePriority() {
        return schedulePriority;
    }
    public void setSchedulePriority(int schedulePriority) {
        this.schedulePriority = schedulePriority;
    }
}
