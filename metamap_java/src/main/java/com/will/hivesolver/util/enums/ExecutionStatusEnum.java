package com.will.hivesolver.util.enums;

/**
 * Created by will on 16-7-15.
 */
public enum ExecutionStatusEnum {
    SUBMIITED("已提交", 0),
    RUNNING("运行中", 1),
    DONE("完成", 2);

    private String name;
    private int index;

    private ExecutionStatusEnum(String name, int index) {
        this.name = name;
        this.index = index;
    }

    public static String getName(int index) {
        for (ExecutionStatusEnum c : ExecutionStatusEnum.values()) {
            if (c.get() == index) {
                return c.name;
            }
        }
        return null;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public int get() {
        return index;
    }

    public void set(int index) {
        this.index = index;
    }

}
